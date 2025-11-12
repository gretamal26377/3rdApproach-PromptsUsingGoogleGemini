import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "../components/ui/carousel";

export default {
  title: "UI/Carousel",
  component: Carousel,
  tags: ["autodocs"],
};

export const Basic = {
  render: () => (
    <Carousel className="w-96">
      <CarouselContent>
        <CarouselItem>
          <div className="bg-blue-100 p-8 text-center">Slide 1</div>
        </CarouselItem>
        <CarouselItem>
          <div className="bg-green-100 p-8 text-center">Slide 2</div>
        </CarouselItem>
        <CarouselItem>
          <div className="bg-yellow-100 p-8 text-center">Slide 3</div>
        </CarouselItem>
      </CarouselContent>
    </Carousel>
  ),
};
